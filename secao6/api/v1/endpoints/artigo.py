from typing import List

from fastapi import APIRouter, status, Depends, HTTPException, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.usuario_model import UsuarioBase  # Corrigindo a importação

from core.deps import get_current_user

from core.database import get_session

from schemas.artigo_schema import ArtigoSchema
from models.artigo_model import ArtigoCreate, ArtigoBase, Artigo

router = APIRouter()

# POST Artigo
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ArtigoSchema)
async def post_artigo(artigo: ArtigoSchema, usuario_logado: UsuarioBase = Depends(get_current_user),
                      db: AsyncSession = Depends(get_session)):
    novo_artigo: ArtigoCreate = ArtigoCreate(titulo=artigo.titulo,
                                           descricao=artigo.descricao,
                                           url_fonte=artigo.url_fonte,
                                           usuario_id=usuario_logado.id
                                           )
    db.add(novo_artigo)
    await db.commit()
    
    return novo_artigo

# GET Artigos
@router.get('/', response_model=List[ArtigoSchema])
async def get_artigos(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(Artigo)
        result = await session.execute(query)
        artigos: List[Artigo] = result.scalars().unique().all()

        return artigos

# GET Artigo
@router.get('/{artigo_id}', response_model=ArtigoSchema, status_code=status.HTTP_200_OK)
async def get_artigo(artigo_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(Artigo).filter(Artigo.id == artigo_id)
        result = await session.execute(query)
        artigo: Artigo = result.scalar().unique().one_or_none()

        if artigo:
            return artigo
        else:
            raise HTTPException(detail='Artigo não encontrado', status_code=status.HTTP_404_NOT_FOUND)

# PUT Artigo
@router.put('/{artigo_id}', response_model=ArtigoSchema, status_code=status.HTTP_202_ACCEPTED)
async def put_artigo(artigo_id: int, artigo: ArtigoSchema, db: AsyncSession = Depends(get_session),
                     usuario_logado: UsuarioBase = Depends(get_current_user)):
    async with db as session:
        query = select(Artigo).filter(Artigo.id == artigo_id)
        result = await session.execute(query)
        artigo_up: Artigo = result.scalar().unique().one_or_none()

        if artigo_up:
            if artigo.titulo:
                artigo_up.titulo = artigo.titulo
            if artigo.descricao:
                artigo_up.descricao = artigo.descricao
            if artigo.url_fonte:
                artigo_up.url_fonte = artigo.url_fonte
            if usuario_logado.id != artigo_up.usuario_id:
                artigo_up.usuario_id = usuario_logado.id

            await session.commit()

            return artigo_up
        else:
            raise HTTPException(detail='Artigo não encontrado', status_code=status.HTTP_404_NOT_FOUND)

# DELETE Artigo
@router.delete('/{artigo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_artigo(artigo_id: int, db: AsyncSession = Depends(get_session),
                     usuario_logado: UsuarioBase = Depends(get_current_user)):
    async with db as session:
        query = select(Artigo).filter(Artigo.id == artigo_id)
        result = await session.execute(query)
        artigo_del: Artigo = result.scalar().unique().one_or_none()

        if artigo_del:
            await session.delete(artigo_del)
            await session.commit()

            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(detail='Artigo não encontrado', status_code=status.HTTP_404_NOT_FOUND)
